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
import {
  CreateCachePolicyRequest,
  CreateCachePolicyResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateCachePolicyCommandInput
  extends CreateCachePolicyRequest {}
export interface CreateCachePolicyCommandOutput
  extends CreateCachePolicyResult,
    __MetadataBearer {}
export declare class CreateCachePolicyCommand extends $Command<
  CreateCachePolicyCommandInput,
  CreateCachePolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateCachePolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateCachePolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<CreateCachePolicyCommandInput, CreateCachePolicyCommandOutput>;
  private serialize;
  private deserialize;
}
