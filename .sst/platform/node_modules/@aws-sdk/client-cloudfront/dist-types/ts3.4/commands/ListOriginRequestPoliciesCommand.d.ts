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
  ListOriginRequestPoliciesRequest,
  ListOriginRequestPoliciesResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListOriginRequestPoliciesCommandInput
  extends ListOriginRequestPoliciesRequest {}
export interface ListOriginRequestPoliciesCommandOutput
  extends ListOriginRequestPoliciesResult,
    __MetadataBearer {}
export declare class ListOriginRequestPoliciesCommand extends $Command<
  ListOriginRequestPoliciesCommandInput,
  ListOriginRequestPoliciesCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListOriginRequestPoliciesCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListOriginRequestPoliciesCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListOriginRequestPoliciesCommandInput,
    ListOriginRequestPoliciesCommandOutput
  >;
  private serialize;
  private deserialize;
}
