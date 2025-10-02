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
import { DeleteOriginRequestPolicyRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteOriginRequestPolicyCommandInput
  extends DeleteOriginRequestPolicyRequest {}
export interface DeleteOriginRequestPolicyCommandOutput
  extends __MetadataBearer {}
export declare class DeleteOriginRequestPolicyCommand extends $Command<
  DeleteOriginRequestPolicyCommandInput,
  DeleteOriginRequestPolicyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteOriginRequestPolicyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteOriginRequestPolicyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteOriginRequestPolicyCommandInput,
    DeleteOriginRequestPolicyCommandOutput
  >;
  private serialize;
  private deserialize;
}
