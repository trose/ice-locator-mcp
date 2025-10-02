import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { DeleteCachePolicyRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteCachePolicyCommandInput
  extends DeleteCachePolicyRequest {}
export interface DeleteCachePolicyCommandOutput extends __MetadataBearer {}
export declare class DeleteCachePolicyCommand extends $Command<
  DeleteCachePolicyCommandInput,
  DeleteCachePolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteCachePolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteCachePolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<DeleteCachePolicyCommandInput, DeleteCachePolicyCommandOutput>;
  private serialize;
  private deserialize;
}
